from setuptools import find_packages, setup


setup(
	name='iscram-server',
	version='1.0.0',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"jsons==1.4.0",
		"pydantic==1.7.3",
		"pytest==6.2.2",
		"uvicorn==0.11.3",
		"numpy==1.20.1",
		"fastapi==0.63.0"
	],
)
