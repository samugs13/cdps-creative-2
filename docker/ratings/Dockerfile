FROM node:12.18.1-slim
ARG service_version
ENV SERVICE_VERSION ${service_version:-v1}
EXPOSE 9080
RUN apt update
RUN apt install git -y
RUN git clone https://github.com/CDPS-ETSIT/practica_creativa2.git
WORKDIR practica_creativa2/bookinfo/src/ratings
RUN mkdir /opt/microservices
RUN cp package.json ratings.js /opt/microservices/
WORKDIR /opt/microservices/
RUN npm install
CMD [ "node", "ratings.js", "9080" ]
