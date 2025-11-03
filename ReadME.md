# Newsletter Project

## 1. Project Overview
**Newsletter** is a Django-based web application designed for publishing and managing articles, newsletters, and user subscriptions. It supports multiple user roles — Readers, Journalists, Editors, and Publishers — each with specific permissions to ensure a smooth workflow and proper oversight of content.

### Key Features
- Custom user registration and authentication (`CustomUser` model)
- Readers can view articles, subscribe to authors and publishers, and receive email notifications
- Journalists can submit and edit articles and newsletters
- Editors can approve, reject, edit, or delete content but **cannot create** new articles or newsletters
- Publishers can manage journalists, approve final content, and oversee all publications
- Automatic email notifications are sent to subscribers when approved articles or newsletters are published
- REST API endpoints allow external integration through `views_api.py` and `urls_api.py`
- Role-based dashboards ensure every user has tailored access and permissions

---

## 2. User Roles and Permissions

### **Reader**
- Can view all approved articles and newsletters  
- Can subscribe to publishers or journalists  
- Receives email notifications when subscribed authors or publishers release approved content  

### **Journalist**
- Can create and edit **articles** and **newsletters**  
- Cannot approve or publish their own work — all submissions require editor approval  
- Can view status updates of submitted content (e.g., Pending, Approved, or Rejected)

### **Editor**
- Can view, approve, reject, edit, or delete any article or newsletter  
- **Cannot create** new articles or newsletters  
- Ensures content quality and compliance before publication  

### **Publisher**
- Can view and manage all journalists under their organization  
- Has authority to approve and publish content from their associated journalists  
- Oversees subscriptions, ensuring readers receive content promptly  

---

## 3. Notifications System

Once an article or newsletter is approved by an editor or publisher:
- An **email notification** is automatically sent to all subscribers of the respective journalist and/or publisher  
- A **tweet** is also sent from the linked X (Twitter) account (if credentials and API access allow)

If Twitter posting fails due to API restrictions, the system continues running without interruption — email delivery remains unaffected.

---

## 4. Subscription Logic

Users can subscribe to:
- **Publishers:** to receive updates from all journalists associated with that publisher  
- **Journalists:** to receive all independent and publisher-linked posts from that journalist  

When a new article or newsletter is published:
- Subscribers of the journalist always receive it (even if it’s independent)  
- Subscribers of a publisher receive it only if the journalist’s content is published under that publisher  

---

## 5. Folder Structure Overview

The project folder is organized as follows, in descending order:

1. **newsletter/** — The main project directory  
   - **manage.py** — The primary Django management script  
   - **README.md** — Documentation for the project  
   - **requirements.txt** — List of dependencies used in the project  
   - **db.sqlite3** — Local development database  
   - **Dockerfile** — Container setup for Docker deployment  
   - **news/** — Main application folder containing all logic  
     - **views.py** — Contains all view functions for handling requests  
     - **models.py** — Defines database models for articles, users, and subscriptions  
     - **forms.py** — Contains Django form classes for creating and editing data  
     - **urls.py** — URL routing configuration for the app  
     - **twitter_api.py** — Handles integration with X (Twitter) API  
     - **notifications.py** — Manages email and tweet notifications for subscribers  
     - **templates/news/** — Contains all HTML templates for rendering pages  
       - **create_article.html**  
       - **create_newsletter.html**  
       - **journalist_dashboard.html**  
       - **editor_dashboard.html**  
       - **additional templates for publishers, readers, etc.**  
   - **docs/** — Generated Sphinx documentation  

---

## 6. Setup Instructions

### A. Using Virtual Environment (venv)

1. Clone the repository:

```bash
git clone <your-public-repo-url>
cd Newsletter
