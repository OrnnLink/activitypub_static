+++
title = "Running an ActivityPub Server Leveraging Static Web Hosting"
date = 2024-08-09T10:34:39+10:00
draft = false
summary = """
Implementing a system capable of running an ActivityPub server on a static web host.
"""
+++

## Objective {#objective}

This project aims to explore the integration of an ActivityPub server into a static site. By investigating the functionalities offered by the ActivityPub protocol, we analyse and test which features can be implemented independently on a static site and which require human intervention or server-side processing.

Notably, we focus on implementing a subset of activities listed on [W3.org](https://www.w3.org/ns/activitystreams) using a static site. Some features can be enabled by simply adding the `Content-Type: application/activity+json` header. However, others necessitate server-side processing to handle incoming requests and generate appropriate responses.

For this project, we have prioritized the implementation of the following functionalities:

### Priority 1 Features:
- [Allowing someone to follow you]()
- [Publishing a post]()
- [Viewing replies to your post]()
- [Replying to a post]()

### Priority 2 Features:
- [Liking a post]()
- [Seeing who liked your post]()
- [Boosting/Announcing a person's post]()
- [Seeing who boosted/announced your post]()
- [Following someone]()

### Priority 3 Features:
- [Bookmarking a post]()
