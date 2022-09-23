#  In this project we have 4 basic models(User,Projects,Work History and Comment) In this app, you can create projects and you can create work histories related to these projects also you can create comments related to these work histories. In short, you can think of it in a Trello-style application logic. Additionally, there is an infrastructure to query work histories and send messages over Slack according to the work history status. You can view how to create all builds on swagger documentation (/docs)

## Before start app, you should add your slack_bot_token and and slack_channel_name to config.json file(if you want to get message about work histories)

## To start app, you should type "docker-compose up --build"(Make sure that you have docker and it is working)

## After app starts, from this url http://127.0.0.1:8000/docs, you can reach the swagger and you can see all endpoints.

## To register, you should go http://127.0.0.1:8000/register
![Ekran görüntüsü 2022-09-23 150640](https://user-images.githubusercontent.com/50598846/191961024-c028d5b9-2d28-485d-b7a7-5ef3eb1d0f11.jpg)

## To login, you should go http://127.0.0.1:8000/login and from here you can get "access_token"
![Ekran görüntüsü 2022-09-23 150715](https://user-images.githubusercontent.com/50598846/191961072-a9412fd5-d52e-4b0f-8dac-e673e8203357.jpg)

## After you get access_token, you should add this token as Bearer token to your requests
![Ekran görüntüsü 2022-09-23 153359](https://user-images.githubusercontent.com/50598846/191961205-4fbc09f1-adfe-4362-882f-24fbce3744c3.jpg)

## Example request with access_token
![Ekran görüntüsü 2022-09-23 150924](https://user-images.githubusercontent.com/50598846/191961318-1b9bb329-6f0e-4664-9733-d07d96a7a436.jpg)
