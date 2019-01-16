CREATE DATABASE MediaManager;

CREATE TABLE Users (
    userID int NOT NULL AUTO_INCREMENT,
    username varchar(32) NOT NULL,
    passwordHash binary(60) NOT NULL,
    settingsAccessLevel TINYINT NOT NULL,
    mediaAccessLevel TINYINT NOT NULL,
    lastFailedLogin int(11),
    loginAttempts TINYINT,
    failedLogins TINYINT,
    failedLoginsLastReset int(11),
    accountState TINYINT NOT NULL,
    PRIMARY KEY (userID)
);

CREATE TABLE User_Watching (
    userID int NOT NULL,
    catalogueIndex int NOT NULL,
    elapsedTime SMALLINT NOT NULL,
    PRIMARY KEY (userID, catalogueIndex)
);

CREATE TABLE User_Tags (
    userID int NOT NULL,
    tagID int NOT NULL,
    catalogueIndex int NOT NULL,
    tagName varchar(255) NOT NULL,
    tagDesc varchar(255) NOT NULL,
    PRIMARY KEY (userID, tagID, catalogueIndex)
);

CREATE TABLE Catalogue (
    keyIndex int NOT NULL AUTO_INCREMENT,
    title varchar(50),
    series_album TINYINT,
    episode_track TINYINT,
    director_artist varchar(50),
    castMembers varchar(255),
    fileType varchar(255),
    fileLocation varchar(255),
    mediaType varchar(255),
    year SMALLINT,
    synopsis varchar(255),
    thumb char(32),
    catagories varchar(255),
    reviews varchar(255),
    PRIMARY KEY (keyIndex)
);

CREATE TABLE Banned_IP (
    IP VARBINARY(16) NOT NULL,
    banDate int NOT NULL
);