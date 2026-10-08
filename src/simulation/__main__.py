"""支持 `python -m simulation` 调用 CLI（spec 0003）。"""

from .cli import main

raise SystemExit(main())
