from app.__init__ import create_app


def run(
        host='127.0.0.1',
        port=4000,
):
    """
    Run RESTful API Server.
    """

    # Create the Flask app
    app = create_app()

    # Return the app to the runner state so it gets actually loaded.
    return app.run(host=host, port=port)


if __name__ == '__main__':
    run()
