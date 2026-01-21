import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_eLdcSE4BHz5s@ep-nameless-cell-a4qzkz8e-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

from sqlalchemy import create_engine, text

engine = create_engine(os.environ['DATABASE_URL'])

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM "EVENTO"'))
    print(f"Eventos en DB: {result.scalar()}")
    
    result2 = conn.execute(text('SELECT COUNT(*) FROM "LOCALIDAD"'))
    print(f"Localidades en DB: {result2.scalar()}")
    
    result3 = conn.execute(text('SELECT id, nombre FROM "EVENTO" LIMIT 5'))
    print("\nPrimeros eventos:")
    for row in result3:
        print(f"  - {row[0]}: {row[1]}")
