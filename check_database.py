from pathlib import Path
import sqlite3

folder = Path(__file__).resolve().parent
name = 'student individual university system.db'
path = folder / name
print('Project folder:', folder)
print('Expected database:', path)
print('Database exists:', path.is_file())
print('Files in project folder:')
for f in sorted(folder.iterdir()):
    if f.is_file():
        print('  ', f.name)
if not path.is_file():
    raise SystemExit('ERROR: database filename does not match. Do not rename or overwrite your original file.')
with sqlite3.connect(f'file:{path.as_posix()}?mode=ro', uri=True) as db:
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    print('Tables:', ', '.join(sorted(tables)))
    required = {'Students', 'Courses', 'Enrollments'}
    if not required.issubset(tables):
        raise SystemExit('ERROR: wrong or empty database. Required tables missing.')
    print('Students:')
    for row in db.execute('SELECT StudentID, FirstName, LastName, Email FROM Students ORDER BY StudentID'):
        print('  ', *row)
print('DATABASE CHECK PASSED')
