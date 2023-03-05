from setuptools import setup

setup(
    name='ReneTelegramBot',
    install_requires=["RenePython==0.9"
                    ,"APScheduler==3.6.3"
                      ,"backports.zoneinfo==0.2.1"
                      ,"cachetools==4.2.2"
                      ,"certifi==2021.10.8"
                      ,"importlib-resources==5.4.0"
                      ,"python-telegram-bot==13.10"
                      ,"pytz==2021.3"
                      ,"pytz-deprecation-shim==0.1.0.post0"
                      ,"six==1.16.0"
                      ,"tornado==6.1"
                      ,"tzdata==2021.5"
                      ,"tzlocal==4.1"
                      ,"zipp==3.6.0"
                      ],
    version='1.1',
    packages=['ReneTelegramBot', 'ReneTelegramBot.Clases', 'ReneTelegramBot.Utiles'],
    description="genial",
    author="René Lázaro Collado Arteaga",
    author_email="renearteaga261998@gmail.com",
    license="GPLv3",
    include_package_data=True,
    classifiers = ["Programming Language :: Python :: 3",
	"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
	"Development Status :: 4 - Beta", "Intended Audience :: Developers",
	"Operating System :: OS Independent"],
    url="https://github.com/critBus/ReneTelegramBot",
)
