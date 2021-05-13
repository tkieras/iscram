from setuptools import find_packages, setup

setup(
	name='iscram-server',
	version='1.0.0',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"jsons==1.4.0",
		"pydantic==1.7.4",
		"uvicorn==0.11.7",
		"fastapi==0.63.0",
		"pytest==6.2.2",
		"pyomo==5.7.3"
	],
)
