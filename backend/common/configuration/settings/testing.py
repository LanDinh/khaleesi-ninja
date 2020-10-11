"""Testing settings for khaleesi.ninja."""

# pylint: disable=unused-wildcard-import

# khaleesi.ninja
from ._base import *  # pylint: disable=wildcard-import


# Test settings.
SECRET_KEY = 'c-@llw&)*y2ny)thn13@84z!b%_(njk#6f@#r+d13j@qa0apze'


# Database.
DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = ''
DATABASES['default']['USER'] = 'khaleesi_ninja'
DATABASES['default']['PASSWORD'] = ''
