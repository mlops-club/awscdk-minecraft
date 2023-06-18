FROM node:19

WORKDIR /app

COPY ./package.json ./package.json
RUN npm install --force
RUN npm audit fix || echo "fixed what we could :|"

COPY ./ ./

ENTRYPOINT [ "npm", "run" ]
CMD build
