# 🚀 NestJS Enterprise Starter

Production-ready NestJS boilerplate with authentication, authorization, and enterprise patterns.

## ✨ Features

- **JWT Auth** — Access token (15m) + Refresh token (7d) rotation
- **Role-based access** — SUPER_ADMIN | ADMIN | USER
- **Security** — Rate limiting, bcrypt, timing-attack protection, PII masking
- **Winston Logger** — Structured JSON logs (production) / pretty logs (development)
- **TypeORM** — PostgreSQL with migration support
- **Swagger** — Auto-generated API docs at `/api/v1/docs`
- **Health check** — DB + memory heap at `/api/v1/health`
- **Validation** — class-validator with whitelist strategy

## 🛠 Tech Stack

- NestJS 10, TypeScript 5, TypeORM 0.3, PostgreSQL
- Passport JWT, bcrypt, Winston, Swagger

## 🚀 Quick Start

\```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/nestjs-enterprise-starter.git
cd nestjs-enterprise-starter

# 2. Install
npm install

# 3. Environment
cp .env.example .env
# add DATABASE_URL, JWT_SECRET, JWT_REFRESH_SECRET at .env

# 4. Run
npm run start:dev
\```

API: http://localhost:3000/api/v1  
Docs: http://localhost:3000/api/v1/docs

## 📁 Project Structure

\```
src/
├── config/          # env validation, typeorm, logger config
├── database/        # database module
├── common/
│   ├── base/        # AuditBaseEntity
│   ├── decorators/  # @GetUser, @Roles, @Public
│   ├── guards/      # JwtAuthGuard, RolesGuard
│   ├── filters/     # HttpExceptionFilter
│   ├── interceptors/# TransformInterceptor
│   └── health/      # health check
└── modules/
    ├── auth/        # register, login, logout, refresh
    └── users/       # user entity & service
\```

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `PORT` | Server port (default: 3000) |
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Access token secret (min 64 chars) |
| `JWT_REFRESH_SECRET` | Refresh token secret (min 64 chars) |
| `NODE_ENV` | development \| production |
| `LOG_LEVEL` | debug \| info \| warn \| error |
| `ALLOW_SYNC` | true only in development |

## 📬 Postman Collection

`ProjectX-Backend.postman_collection.json`

## 📄 License

MIT
