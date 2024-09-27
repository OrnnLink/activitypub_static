# The process behind Create User

**Aim** - Creates a user on the static site, with data structures for storing relevant information regarding the newly created user.

**Note**:
- You can have multiple users exists in the system at a time, but only one of the user can be discovered by other ActivityPub platform at one time. 

## How to Create a new user?

To create a new user Navigate to `/application/activities` directory and open the `webfinger_activity.json`. You should see the following json structure:
```json
{
    "username": "",
}
```
For example, if you set the `username` to be `noah`, the system would creates the new user `noah`, with his/her webfinger, and relevant actor object files. 

## How it works?
By setting the field `username` to other values, the system would first check if the user already exists in the system then updates the static site webfinger. Otherwise, it creates the numerous files to support ActivityPub protocol using the data from `config.json` provided. 

An example `config.json`:
```json 
{
    "username": "noah",
    "domain": "staticap.netlify.app",
    "site_dir_path": "../activitypub",
    "public_key_path": "...",
    "private_key_path": "..."
}
```

First, using the `site_dir_path` the system can determine where to find your hugo project, and its `/static` directory. It then creates the folders `/static/.well-known`, and the text file `webfinger` with the following structure:
```json
{
    "aliases": [],
    "links": [
        {
            "href": "https://DOMAIN/USERNAME/user-info/actor.json",
            "rel": "self",
            "type": "application/activity+json"
        }
    ],
    "subject": "acct:USERNAME@DOMAIN"
}
```
Afterwards, the system would proceed to creates the following structure inside the hugo project:
```
`static`
-`noah`
--`user-info`
---`actor.json`
---`followers.json`
---`following.json`
---`outbox.json`
---`inbox.json`
---`followers.json`
---`followers`
----`first.json`
---`following`
----`first.json`
---`outbox`
----`first.json`
---`inbox`
----`first.json`
```

For caching purposes, it will also creates the following structure inside the `/application/resources/users/USERNAME`:
```
`USERNAME`
-`followers.json`: Stores a list of webfingers of people that has followed this user.
-`following.json`: Stores a list of webfingers that this user has followed.
-`posts.json`: Stores a list of post ids that have been posted by this user.
```