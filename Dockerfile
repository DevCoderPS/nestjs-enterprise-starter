# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: deps — install all dependencies (cached layer)
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps

RUN apk add --no-cache python3 make g++

WORKDIR /app

COPY package*.json ./
RUN npm ci --frozen-lockfile

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: builder — compile TypeScript
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN npm run build

# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: production — lean final image
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS production

RUN addgroup -g 1001 -S nodejs && \
    adduser  -u 1001 -S nestjs -G nodejs

WORKDIR /app

COPY package*.json ./
RUN npm ci --frozen-lockfile --omit=dev && \
    npm cache clean --force

COPY --from=builder /app/dist ./dist

RUN mkdir -p logs && chown -R nestjs:nodejs /app

USER nestjs

EXPOSE 3000

CMD ["node", "dist/main"]
