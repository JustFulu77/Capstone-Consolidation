# Newsletter Project

A Django-based web application for creating, publishing, and managing newsletters and articles with structured user roles and automated subscriber notifications.

## Description

The **Newsletter Project** provides a multi-role publishing platform where readers, journalists, editors, and publishers can work together efficiently. Journalists submit content, editors review and approve, and publishers finalize publication. Readers can subscribe to specific authors or publishers and automatically receive email notifications when new content is released. The system also includes REST API endpoints and optional Twitter (X) integration for automatic post sharing.

## Getting Started

### Dependencies

Before running this project, ensure you have the following installed:

* Python 3.11+
* Django 5.2.7
* MySQL (or SQLite for development)
* pip (Python package manager)
* Docker (optional)

All Python dependencies are listed below (from `requirements.txt`):


### Installing

Follow the steps below to set up the project locally:

1. Clone the repository
2. Create a virtual environment
3. Activate the virtual environment
4. Install all required dependencies
5. Create a `.env` file in the project root with your environment variables
6. Run migrations to prepare your database
7. Start the development server

Once running, open your browser and go to **http://127.0.0.1:8000**.

### Executing Program

To run the program using Docker:

1. Build the Docker image:

2. Run the Docker container:


Access the app at **http://localhost:8000** after the container starts.

## Help

If you run into common issues, try the following:

* **Server not starting:** Check that `.env example.txt` for instructions.
* **Database errors:** Ensure your `DATABASE_URL` is correct and that MariaDB is running properly.
* **Docker not building:** Make sure Docker Desktop or the Docker Engine service is running on your system.

You can also verify your Django configuration by running:


## Authors

**Fulufhelo Ganyane**  
GitHub: [JustFulu77](https://github.com/JustFulu77)

## Version History

* 0.2  
    * Added Docker support and improved Sphinx documentation  
    * Updated README for better setup clarity  
    * See [commit history](https://github.com/JustFulu77/Capstone-Consolidation/commits)

* 0.1  
    * Initial release of Newsletter project  

## License

This project currently has **no license**.

## Acknowledgments

Inspiration, tools, and references used:

* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)
