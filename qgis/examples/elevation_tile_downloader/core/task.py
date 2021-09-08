from qgis.core import (QgsTask,
                       QgsMessageLog,
                       Qgis,
                       QgsRasterLayer,
                       QgsProject,
                       QgsNetworkAccessManager,
                       QgsNetworkReplyContent,
                       QgsGeometry
                       )
from PyQt5.QtCore import QFileInfo, QUrl, pyqtSignal
from qgis.PyQt.QtNetwork import QNetworkRequest
from typing import List
from pathlib import Path
import traceback
import gzip
from io import BytesIO


class DownloadTask(QgsTask):
    next_tile = pyqtSignal(int)

    def __init__(self, grid: List[QgsGeometry], output_dir, add=False):
        super().__init__("Tile download task", QgsTask.CanCancel)
        self.grid = grid
        self.output_dir = output_dir
        self.exception = None
        self.traceback = None
        self.total = len(self.grid)
        self.add = add
        self.tiles_downloaded: List[Path] = []
        self.nam = QgsNetworkAccessManager()

    def run(self):
        QgsMessageLog.logMessage(
            message='Started task {}'.format(self.description()),
            level=Qgis.Info
        )
        try:
            for i, poly in enumerate(self.grid):
                self.next_tile.emit(i)
                x, y = poly.boundingBox().xMinimum(), poly.boundingBox().yMinimum()
                self.prepare_dir(y, self.output_dir)
                tile_name = '%s%02d%s%03d.hgt' % ('S' if y < 0 else 'N', abs(y), 'W' if x < 0 else 'E', abs(x))
                dir_name = '%s%02d' % ('S' if y < 0 else 'N', abs(y))
                url = QUrl(f"http://s3.amazonaws.com/elevation-tiles-prod/skadi/{dir_name}/{tile_name}.gz")
                request_ = QNetworkRequest(url)
                dest_directory = Path(self.output_dir, dir_name)
                filepath = Path(dest_directory, tile_name)
                if not filepath.is_file():
                    reply: QgsNetworkReplyContent = self.nam.blockingGet(request_)
                    length = int(reply.rawHeader(bytes('Content-Length'.encode())))
                    stream = BytesIO(reply.content())
                    with gzip.GzipFile(fileobj=stream, mode='rb') as gz:
                        with open(filepath, 'wb') as f:
                            processed = 0
                            chunk_size = 1024 ** 2
                            while True:
                                chunk = gz.read(chunk_size)
                                if not chunk:
                                    break
                                f.write(chunk)
                                processed += chunk_size
                                self.setProgress((processed / length) * 100)  # goes to 90-something percent real fast and then stays there for another couple of seconds or so...
                else:
                    QgsMessageLog.logMessage(
                        message=f"Already downloaded tile {url.url()}", level=Qgis.Info
                    )
                self.tiles.append(filepath)
                if self.isCanceled():
                    return False
            return True
        except Exception as e:
            self.exception = e
            self.traceback = traceback.format_exc()
            return False

    def finished(self, result):
        if result:
            QgsMessageLog.logMessage(
                message=f'Finished downloading tiles. {len(self.tiles)} tiles downloaded.',
                level=Qgis.Info
            )
            if self.add:
                self.add_to_map()
        elif not result and self.exception:
            QgsMessageLog.logMessage(
                message=f'An exception occurred during downloading: {self.exception}\n'
                        f'{self.traceback}',
                level=Qgis.Warning
            )
        elif not result and not self.exception:
            QgsMessageLog.logMessage(
                message=f'Canceled download task. {len(self.tiles_downloaded)} tiles downloaded.',
                level=Qgis.Warning
            )

    @staticmethod
    def prepare_dir(y, dest_dir):
        dir_name = '%s%02d' % ('S' if y < 0 else 'N', abs(y))
        directory = Path(dest_dir, dir_name)
        Path.mkdir(directory, exist_ok=True)

    def add_to_map(self):
        project = QgsProject.instance()
        for tile_path in self.tiles_downloaded:
            finfo = QFileInfo(str(tile_path))
            base_name = finfo.baseName()
            path = finfo.filePath()
            if base_name and path:
                raster: QgsRasterLayer = QgsRasterLayer(path, base_name)
                if not raster.isValid():
                    QgsMessageLog.logMessage(
                        message=f'Raster not valid: {str(tile_path)}',
                        level=Qgis.Warning
                    )
                else:
                    project.addMapLayer(raster)
