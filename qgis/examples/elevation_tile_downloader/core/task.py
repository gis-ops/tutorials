from typing import List, Optional, Set
from pathlib import Path
import gzip
from io import BytesIO

from qgis.gui import QgisInterface
from qgis.core import (
    QgsTask,
    QgsMessageLog,
    Qgis,
    QgsRasterLayer,
    QgsProject,
    QgsNetworkAccessManager,
    QgsNetworkReplyContent,
    QgsGeometry,
)
from qgis.utils import iface
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtNetwork import QNetworkRequest

iface: QgisInterface


class DownloadTask(QgsTask):
    def __init__(self, grid: Set[QgsGeometry], output_dir: Path):
        super().__init__("Tile download task", QgsTask.CanCancel)
        self.grid = grid
        self.output_dir = output_dir

        self.exception: Optional[Exception] = None
        self.tiles: List[Path] = []

    def run(self):
        """Do the work."""
        nam = QgsNetworkAccessManager()

        # Don't raise any error during processing, relay error reporting to self.finished()
        try:
            for i, bbox in enumerate(self.grid):
                if self.isCanceled():
                    return False

                # Get the filepath and create the output directory (if necessary)
                x, y = (
                    bbox.boundingBox().xMinimum(),
                    bbox.boundingBox().yMinimum(),
                )
                hemisphere = "S" if y < 0 else "N"
                dir_name = "%s%02d" % (hemisphere, abs(y))
                directory = self.output_dir.joinpath(dir_name)
                directory.mkdir(exist_ok=True)
                tile_name = "%s%02d%s%03d.hgt" % (
                    hemisphere,
                    abs(y),
                    "W" if x < 0 else "E",
                    abs(x),
                )
                filepath = self.output_dir.joinpath(dir_name, tile_name)
                self.tiles.append(filepath)
                if filepath.is_file():
                    QgsMessageLog.logMessage(
                        message=f"Already downloaded tile {tile_name}",
                        level=Qgis.Info,
                    )
                    continue

                # get the new tile if it didn't exist
                url = QUrl(
                    f"http://s3.amazonaws.com/elevation-tiles-prod/skadi/{dir_name}/{tile_name}.gz"
                )
                request = QNetworkRequest(url)
                reply: QgsNetworkReplyContent = nam.blockingGet(request)
                # turn the reply into a file object and write the decompressed file to disk
                with gzip.GzipFile(
                    fileobj=BytesIO(reply.content()), mode="rb"
                ) as gz:
                    with open(filepath, "wb") as f:
                        f.write(gz.read())

                self.setProgress((i / len(self.grid)) * 100)

            return True
        except Exception as e:
            self.exception = e
            return False

    def finished(self, result):
        """Postprocessing after the run() method."""
        if self.isCanceled():
            # if it was canceled by the user
            QgsMessageLog.logMessage(
                message=f"Canceled download task. {len(self.tiles)} tiles downloaded.",
                level=Qgis.Warning,
            )
            return
        elif not result:
            # if there was an error
            QMessageBox.critical(
                iface.mainWindow(),
                "Tile download error",
                f"The following error occurred:\n{self.exception.__class__.__name__}: {self.exception}",
            )
            return

        iface.messageBar().pushMessage(
            "Success",
            f"Finished downloading {len(self.tiles)} tiles.",
            level=Qgis.Success,
        )

        # add the rasters to the map canvas
        for tile_path in self.tiles:
            if not tile_path.exists():
                QgsMessageLog.logMessage(
                    message=f"Tile at {tile_path.resolve()} was removed.",
                    level=Qgis.Warning,
                )
                continue
            QgsProject.instance().addMapLayer(
                QgsRasterLayer(str(tile_path.resolve()), tile_path.stem)
            )
