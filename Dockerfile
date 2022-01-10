FROM ubuntu:20.04

ENV LC_ALL C.UTF-8

RUN mkdir /blog
WORKDIR /blog

RUN apt-get update
RUN apt-get install -y ruby-full libffi-dev ruby-dev make gcc build-essential
RUN gem install jekyll bundler:1.17.2 

COPY Gemfile /blog
COPY Gemfile.lock /blog
RUN bundle install
RUN rm /blog/Gemfil*

EXPOSE 4000

CMD ["bundle","exec","jekyll","serve","--host","0.0.0.0","--incremental"]
