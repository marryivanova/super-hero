from pathlib import Path

from starlette.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent.parent
FRONTEND_ROOT = BASE_DIR / "frontend"
PUBLIC_ASSETS = FRONTEND_ROOT / "public"

templates = Jinja2Templates(directory=str(FRONTEND_ROOT))


title = "SuperHero API Documentation 🦸‍♂️"

description = """

## 📋 Task Description

### 🔹 POST /hero/
**Required parameter:**  
`name` - exact hero name to search  

**Functionality:**  
1. Searches for a hero by name via SuperHero API  
2. Adds found hero to the database  
3. Returns error if hero not found  

### 🔹 GET /hero/
**Optional parameters:**  
- `name` - exact name match  
- `intelligence` - intelligence filter  
- `strength` - strength filter  
- `speed` - speed filter  
- `power` - power filter  

**Filter operators:**  
For numeric parameters supports:  
- `=10` - exact match  
- `>=10` - greater than or equal  
- `<=10` - less than or equal  

**Response:**  
- Returns all heroes matching filters  
- Returns error if no matches found  

"""
