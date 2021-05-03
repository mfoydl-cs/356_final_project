#Social Media Site
 A social media website application built on Flask, similar to those provided by Twitter.
 
 #USAGE
 - Users can create an account, and then login with their credentials after verifying their email.
 - Logged in users can create posts, view their timeline, or search for posts/users.
 - Users can like others posts, repost, or follow users they'd like to appear on their timeline.
 
 #Implementation
 - User/post data is stored on a MongoDB NoSQL Server
 - User recognition uses JWT for authorization
 - Search funtionality is implemented via Elasticsearch
 - Frontend is simple HTML/CSS with vanilla JavaScript
 
 #Notes
 An Ansible script was used to deploy the application from this repo: https://github.com/mfoydl-cs/flask_ansible
