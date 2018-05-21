FROM node

ENV NODEDIR=/nodeapp

RUN mkdir $NODEDIR
WORKDIR $NODEDIR

COPY package.json $NODEDIR/
RUN npm install

COPY . $NODEDIR/

CMD ["npm", "start"]
