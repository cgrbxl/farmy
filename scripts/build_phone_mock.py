"""Keep the supplied mock intact; build an annotated static public copy."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'docs/mock/farmy · Las Tres Encinas.html'
output = ROOT / 'dashboard/mock/index.html'
text = source.read_text()
text = text.replace('<html>', '<html lang="en">', 1)
# The public copy is always a browser simulation. Block every network API call,
# including the original client's dormant fallback to a future /api server.
head = '''<meta name="description" content="Explore Farmy's future phone experience at fictional Las Tres Encinas, with an optional guide to its nine module families.">
<meta http-equiv="Content-Security-Policy" content="default-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'">
<link rel="stylesheet" href="architecture.css">
'''
text = text.replace('</head>', head + '</head>', 1)
text = text.replace('Reloading the page resets it.', 'Reloading resets the farm simulation; your model selection may remain in this browser. This is a future-solution illustration, not the current production product.')
text = text.replace('</body>', '<script src="architecture.js"></script>\n</body>')
output.write_text(text)
print('Built annotated phone mock; original preserved.')
