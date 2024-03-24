import sys  # Exit the program if an error occurs
import argparse  # Parse command line arguments
from saleapp import app  # The Flask application for the YUAG search application


def main():
    """
    Parse command line arguments and run the server.
    """
    # Accept user-given port to run the server and listen on
    parser = argparse.ArgumentParser(
        description="Server for the senior sales application",
        allow_abbrev=False)
    parser.add_argument("port",
                        type=int,
                        help="the port at which the server should listen")
    args = parser.parse_args()

    try:
        app.run(port=args.port,  # Listen on the given port
                host="0.0.0.0",  # Listen on all IP addresses
                debug=True)  # Verbose error messages (for development only)
    except OSError as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
