"""PetGarden CLI：serve。"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="petgarden", description="PetGarden 班级宠物园")
    sub = parser.add_subparsers(dest="command", required=True)

    serve_p = sub.add_parser("serve", help="启动服务（默认 127.0.0.1:8000）")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn

        from petgarden.config import Settings
        from petgarden.main import create_app

        app = create_app(Settings())
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()