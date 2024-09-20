+++
title = 'Webfinger For Discovery'
date = 2024-07-18T14:11:45+10:00
draft = false
tags = [ 'Static-Site', 'ActivityPub' ]
summary = """
This article contains information about the fundamental of webfinger, and how to setup your webfinger and actor object on your static site, such that they can be discovered by other ActivityPub instances.
"""
[seeNext]
	signing_algorithms = "/extra/signing_algorithm"
	implementing_follow = "/page/implementing_follow"
	implementing_post = "/page/implementing_post"
+++

## Webfinger Fundamental

Webfinger is often used to idenify a user profile under a specific domain. By definition, a user webfinger can be separated into two pieces to help platforms, such as Pleroma, Mastodon, Ktistec, etc., to discover and retrieved relevant information about your profile. Take for instance, {{< pretty-code >}}@noah@mastodon.social{{< /pretty-code >}}, the first part of the webfinger `@noah` is used to identifed the user of the domain `@mastodon.social`. 

When a user on an Activity Pub Platform look up another person (i.e. Bob lookup noah), many of the ActivityPub platform would attempt to look for the user **noah** locally on the instance first, before making a request to `@domain` provided by the webfinger. 
 
The instance typically makes a request to {{< pretty-code >}}https://domain/.well-known/webfinger{{< /pretty-code >}}, with the following parameter {{< pretty-code >}}?resource=acct:user@domain{{< /pretty-code >}}. For our example, it would be `https://mastodon.social/.well-known/webfinger?resource=acct:noah@mastodon.social`.

## Setting up Webfinger

Now that we understand how ActivityPub uses Webfinger to look up a user on your domain. We can start focusing on building the minimal setup such that a user on our site can be discovered by other ActivityPub instances.

To do this, we will utilise Hugo as our static-site generator (SSR) framework, and Netlify as our deploying services. It's important to note, as of now, it is now possible to make your webfinger discoverable if you are choosing Github Page as your deploying services. The problem is most ActivityPub instances requires the field {{< pretty-code >}}Content-Type: application/activity+json{{< /pretty-code >}} inside the headers, and Github does not allow developer to make any modification to the headers. We will bypass this system, by using Netlify as our deployment method, it is also possible to setup custom headers, if you are using custom domain too.

After setting up the basic layout of your hugo project, you need to create a new plain-text file without any extension, under {{< pretty-code >}}/static/.well-known/webfinger{{< /pretty-code >}}. Inside the `webfinger` file, we'll setup the following JSON structure:

```json
{
	"subject": "acct:USERNAME@YOUR_DOMAIN",
	"aliases": [],
	"links": {
		"rel": "self",
		"type": "application/activity+json",
		"href": "https://YOUR_DOMAIN/USERNAME/actor.json"
	}
}
```

Let {{< pretty-code >}}USERNAME=noah{{< /pretty-code >}} and {{< pretty-code >}}YOUR_DOMAIN=noah.netlify.app{{< /pretty-code >}}, our webfinger structure becomes:

```json
{
	"subject": "acct:noah@noah.netlify.app",
	"aliases": [],
	"links": {
		"rel": "self",
		"type": "application/activity+json",
		"href": "https://noah.netlify.app/noah/actor.json"
	}
}
``` 

Under the aliases section, you can include any relevant link that directs the user to your {{< pretty-code >}}text/html{{< /pretty-code >}} document, representing your actor object. For instance, the user can find someone mastodon aliases under {{< pretty-code >}}https://mastodon.social/@USERNAME{{< /pretty-code >}} or {{< pretty-code >}}https://mastodon.social/users/USERNAME{{< /pretty-code >}}

## Setting Up Your Actor Object

After setting up your webfinger, we'll need to create {{< pretty-code >}}/static/noah{{< /pretty-code >}} with noah is the username we used in our previous example. Inside the noah folders, we are gonna need to create the following json files: 
1. actor.json 
2. followers.json - can be empty
3. following.json - can be empty
4. inbox.json - can be empty
5. outbox.json - can be empty

The structure of actor.json is as followed:

```json
{
	"@context": "https://www.w3.org/ns/activitystreams",
	"type": "Person",
	"preferredUsername": "noah",
	"id": "https://noah.netlify.app/noah/actor.json",
	"inbox": "https://noah.netlify.app/noah/inbox.json",
	"outbox": "https://noah.netlify.app/noah/outbox.json",
	"followers": "https://noah.netlify.app/noah/followers.json",
	"following": "https://noah.netlify.app/noah/following.json",
	"publicKey": {
		"id": "https://noah.netlify.app/noah/actor.json#main-key", 
		"owner": "https://noah.netlify.app/noah/actor.json",
		"publicKeyPem": "..."
	}
}
```

Your public key can be generated via the following javascript code: 

```javascript
// generate-keys.js

const { generateKeyPairSync } = require('crypto');
const fs = require('fs');

const { publicKey, privateKey } = generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: {
    type: 'pkcs1',
    format: 'pem'
  },
  privateKeyEncoding: {
    type: 'pkcs1',
    format: 'pem'
  }
});

// Save the keys to files
fs.writeFileSync('public_key.pem', publicKey);
fs.writeFileSync('private_key.pem', privateKey);

// Printing out the public and private keys
console.log('Public Key:', publicKey);
console.log('Private Key:', privateKey);

```

After generating your public key and filling it inside {{< pretty-code >}}publicKeyPem{{< /pretty-code >}}, you would then need to make sure that the `Content-Type` for {{< pretty-code >}}/noah/actor.json{{< /pretty-code >}} end point, to be {{< pretty-code >}}application/activity+json{{< /pretty-code >}}. Using netlify, this can be done by creating a file `netlify.toml` at the root directory of your github project and adds the following lines
```toml
[[headers]]
for = "/noah/*"
[headers.values]
Content-Types = "application/activity+json"
```

By completing all the steps above, ActivityPub platforms can now discovered a user on your static site via Webfinger.

---

**References** 
- [Adding ActivityPub to Your Static Site - Paul Kinlan](https://paul.kinlan.me/adding-activity-pub-to-your-static-site/)
- [Understanding Webfinger](https://webfinger.net/)
- [Mastodon Webfinger](https://docs.joinmastodon.org/spec/webfinger/)

