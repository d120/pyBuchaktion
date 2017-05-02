# pyBuchaktion #

pyBuchaktion is a Django application for the [Buchaktion of the Fachschaft Informatik](https://www.d120.de/de/studierende/buchaktion/).

The purpose of the app is to build an interface for participants of the Buchaktion. Further it manages the organisation tasks for the members of the Buchaktionsteam.

Development
----
Everyone with interest in helping us, should now that:
* for testing use the D120 Django CMS. 
 * Read [this](https://github.com/d120/pyBuchaktion/wiki/Testing-with-D120-Django-CMS) for further instructions.
* we have decided to use the workflow recommended by GitHub. This means:
 * new feature = new branch
 * After creating a branch and making one or more commits, a Pull Request starts the conversation around the proposed changes.
 * Additional commits are commonly added based on feedback before merging the branch.

Documentation
----
You can find information, a manual and furthermore in the Wiki of this project. 

Deployment
----------

To use pyBuchaktion, you will need to configure [pyTUID](https://github.com/d120/pyTUID). As pip currently does not provide a preferred dependency resolution workflow for privately hosted projects, you'll need to start pip with `--process-dependency-links`.

License
----
Files in pyBuchaktion are licensed under the Affero General Public License version 3, the text of which can be found in LICENSE, or any later version of the AGPL, unless otherwise noted.
