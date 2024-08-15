+++
title = "Running an ActivityPub Server Leveraging Static Web Hosting"
date = 2024-08-09T10:34:39+10:00
draft = false
summary = """
Setting up a minimal ActivityPub-compatible static site involves integrating an ActivityPub server into the static site. The process includes creating a WebFinger file and an actor object, enabling user discovery by other platforms, along with a curated list of features to be implemented.
"""
+++

## Objective {#objective}

This project aims to explore the integration of an ActivityPub server into a static site. By investigating the functionalities offered by the ActivityPub protocol, we analyse and test which features can be implemented independently on a static site and which require human intervention or server-side processing.

Notably, we focus on implementing a subset of activities listed on [W3.org](https://www.w3.org/ns/activitystreams) using a static site. Some features can be enabled by simply adding the `Content-Type: application/activity+json` header. However, others necessitate server-side processing to handle incoming requests and generate appropriate responses.

For this project, we have prioritized the implementation of the following functionalities:

### Priority 1 Features:
- [Allowing someone to follow you](/page/extra/getting_follow_feature)
- [Publishing a post](/page/extra/publish_post_feature)
- [Viewing replies to your post](/page/extra/getting_replies_feature)
- [Replying to a post](/page/extra/posting_reply_feature)

### Priority 2 Features:
- [Liking a post]()
- [Seeing who liked your post]()
- [Boosting/Announcing a person's post]()
- [Seeing who boosted/announced your post]()
- [Following someone](/page/extra/following_feature)

### Priority 3 Features:
- [Bookmarking a post]()

## Understanding WebFinger

WebFinger is commonly used to identify a user profile associated with a specific domain. It works by separating a user's WebFinger address into two parts, allowing platforms like Pleroma, Mastodon, and Ktistec to discover and retrieve relevant information about your profile. For example, in the address `@noah@mastodon.social`, the first part, `@noah`, identifies the user, while the second part, `@mastodon.social`, identifies the domain.

When a user on an ActivityPub platform searches for another user (e.g., Bob looks up Noah), many platforms will first try to locate the user "Noah" on the local instance. If the user is not found locally, the platform will then make a request to the domain specified by the WebFinger address.

Typically, the instance will send a request to `https://domain/.well-known/webfinger` with the following parameter: `?resource=acct:user@domain`. For our example, the request would be `https://mastodon.social/.well-known/webfinger?resource=acct:noah@mastodon.social.`
Here's a polished version of your text:

Now that we understand how ActivityPub uses WebFinger to look up a user on your domain, we can focus on building the minimal setup needed for users on our site to be discovered by other ActivityPub instances.

To achieve this, we'll use Hugo as our static site generator (SSG) framework and Netlify as our deployment service. It's important to note that, as of now, using GitHub Pages as your deployment service won't allow your WebFinger to be discoverable. This is because most ActivityPub instances require the `Content-Type: application/activity+json` header, and GitHub Pages doesn't allow developers to modify headers. We'll bypass this limitation by using Netlify, which also allows you to set custom headers, especially if you're using a custom domain.

### Setting Up WebFinger

After setting up the basic layout of your Hugo project, create a new plain-text file without any extension under `/static/.well-known/webfinger`. Inside the WebFinger file, set up the following JSON structure:

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

For example, with `USERNAME=noah` and `YOUR_DOMAIN=noah.netlify.app`, your WebFinger structure would be:

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

Under the `aliases` section, you can include any relevant links that direct users to your text/HTML documents representing your actor object. For instance, a user's Mastodon alias might be found under `https://mastodon.social/@USERNAME` or `https://mastodon.social/users/USERNAME`.

### Setting Up Your Actor Object

After configuring your WebFinger, create a `/static/noah` directory (using "noah" as the username in our example). Inside the `noah` folder, create the following JSON files:

- `actor.json`
- `followers.json` (can be empty)
- `following.json` (can be empty)
- `inbox.json` (can be empty)
- `outbox.json` (can be empty)

The structure of `actor.json` should be as follows:

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

Your public key can be generated using the following JavaScript code:

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

// Print out the public and private keys
console.log('Public Key:', publicKey);
console.log('Private Key:', privateKey);
```

After generating your public key, insert it into the `publicKeyPem` field. You then need to ensure that the Content-Type for the `/noah/actor.json` endpoint is set to `application/activity+json`. Using Netlify, this can be achieved by creating a `netlify.toml` file at the root directory of your GitHub project and adding the following lines:

```toml
[[headers]]
for = "/noah/*"
[headers.values]
Content-Type = "application/activity+json"
```

By completing all the steps above, ActivityPub platforms will now be able to discover a user on your static site via WebFinger.

---
**References**
- [Adding ActivityPub to Your Static Site](https://paul.kinlan.me/adding-activity-pub-to-your-static-site/)
- [Understanding WebFinger](https://webfinger.net/)
- [Mastodon WebFinger](https://docs.joinmastodon.org/spec/webfinger/)

---
**See also** 
- [Full codebase](/page/extra/activitypub_codebase)