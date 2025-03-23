ARG UBUNTU_VERSION

FROM ubuntu:${UBUNTU_VERSION}

ENV DEBIAN_FRONTEND noninteractive

ENV AWS_ACCESS_KEY_ID=
ENV AWS_SECRET_ACCESS_KEY=
ENV AWS_DEFAULT_REGION=

ARG TERRAFORM_VERSION
ARG AWSCLI_VERSION

VOLUME /infrastructure

RUN apt update && apt install -y git

RUN apt update && apt install -y wget unzip &&  \
  wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_arm.zip && \
  unzip terraform_${TERRAFORM_VERSION}_linux_arm.zip && \
  mv terraform /usr/local/bin/

RUN apt update && apt install -y zip curl mandoc less jq && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64-${AWSCLI_VERSION}.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip ./aws/install && \
    apt remove -y zip

# session manager plugin
RUN curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_arm64/session-manager-plugin.deb" -o "session-manager-plugin.deb" && \
    dpkg -i session-manager-plugin.deb && \
    rm -rf session-manager-plugin.deb

WORKDIR /infrastructure

ENTRYPOINT ["sleep", "infinity"]
