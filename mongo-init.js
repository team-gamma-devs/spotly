db = db.getSiblingDB('spotly');

db.createUser({
  user: process.env.MONGO_INITDB_ROOT_USERNAME || 'spotly_user',
  pwd: process.env.MONGO_INITDB_ROOT_PASSWORD || 'spotly_password',
  roles: [
    {
      role: 'readWrite',
      db: 'spotly'
    }
  ]
});

print('Usuario de aplicación creado exitosamente');