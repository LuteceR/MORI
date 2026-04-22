FROM node:22

WORKDIR /src

COPY package.json pnpm-lock.yaml ./

RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install --frozen-lockfile --ignore-scripts

COPY . .

EXPOSE 3000

CMD ["pnpm", "dev", "--host"]