# Contenedor del frontend: compila la SPA de Vue con Vite y la sirve con nginx.
# nginx también reenvía /api/* al contenedor del backend, así que el
# navegador solo habla con un origen y no hace falta CORS.

# --- Etapa 1: compilar ---
FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY index.html vite.config.ts tsconfig*.json ./
COPY src/ ./src/

# Las variables VITE_* se meten en el JavaScript al compilar: si cambian,
# hay que reconstruir la imagen. La clave publicable de Clerk puede ser pública.
ARG VITE_CLERK_PUBLISHABLE_KEY
ARG VITE_USE_MOCK=false
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY \
    VITE_USE_MOCK=$VITE_USE_MOCK

RUN npm run build

# --- Etapa 2: servir ---
FROM nginx:1.27-alpine

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
