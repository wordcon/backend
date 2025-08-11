from typing import Annotated

from msgspec import Meta

Email = Annotated[str, Meta(min_length=5, max_length=100, pattern=r'^[^@]+@[^@]+\.[^@]+$')]
Password = Annotated[str, Meta(min_length=8, max_length=128)]
Name = Annotated[str, Meta(min_length=1, max_length=50)]
