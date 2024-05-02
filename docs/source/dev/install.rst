Installation (Dev Version)
==========================================

This guide will walk you through setting up your development environment for the Molara project.

1. **Clone the Repository**
   Begin by cloning the repository to your local machine:

   .. code-block:: bash

       git clone https://github.com/Molara-Lab/Molara.git
       cd Molara

2. **Set up a Virtual Environment**
   It's recommended to use a virtual environment to manage dependencies.

   .. code-block:: bash

       python -m venv Molara-venv

   Activate the virtual environment:

   .. code-block:: bash

       # On Windows
       .\Molara-venv\Scripts\activate
       # On Unix or MacOS
       source Molara-venv/bin/activate

3. **Install Dependencies**
   Install Molara in development mode:

   .. code-block:: bash

       pip install -e .[dev]

Please ensure all steps are followed in order to set up your development environment correctly.
