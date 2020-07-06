CREATE DATABASE MediaManager;
GO

USE [MediaManager]
GO

CREATE TABLE PeopleMetadata (
    PersonId INT NOT NULL IDENTITY(1, 1),
    PersonName VARCHAR(255) NOT NULL,
    PersonRole VARCHAR(255) NOT NULL,

    PRIMARY KEY(PersonId),
    INDEX ActorOr(PersonRole)
);

CREATE TABLE CastMetadata (
    CastId INT NOT NULL IDENTITY(1, 1),
    ActorId INT NOT NULL FOREIGN KEY REFERENCES PeopleMetadata(PersonId),

    PRIMARY KEY(CastId),
    INDEX ActorsCredits(ActorId)
);

CREATE TABLE DirectorsMetadata (
    DirectorsId INT NOT NULL IDENTITY(1, 1),
    DirectorId INT NOT NULL FOREIGN KEY REFERENCES PeopleMetadata(PersonId),

    PRIMARY KEY(DirectorsId),
    INDEX DirectorsCredits(DirectorId)
);

CREATE TABLE MediaMetadata (
    MediaId INT NOT NULL IDENTITY(1, 1),

    ImdbRating Decimal NOT NULL,
    MediaRuntime INT NOT NULL,
    ReleaseDate DATETIME2 NOT NULL,
    Overview TEXT NOT NULL,
    ThumbnailPath VARCHAR(255) NOT NULL,
    ThumbnailUrl VARCHAR(255) NOT NULL,

    CastId INT NOT NULL FOREIGN KEY REFERENCES CastMetadata(CastId),
    DirectorsId INT NOT NULL FOREIGN KEY REFERENCES DirectorsMetadata(DirectorsId),

    SeriesName VARCHAR(100),
    SeriesNumber TINYINT,

    DisplayName VARCHAR(100) NOT NULL,
    EpisodeNumber TINYINT,

    INDEX ActorsCreditsMediaIndex(CastId),
    INDEX DirectorsCreditsMediaIndex(DirectorsId),

    PRIMARY KEY(MediaId)
);

CREATE TABLE FileMetadata (
    FileId INT NOT NULL IDENTITY(1, 1),
	FilePath NVARCHAR(260) NOT NULL,
    DiscoveredBy VARCHAR(15) NOT NULL,

    HasMatchedMedia BIT NOT NULL,
    MatchedMediaId INT FOREIGN KEY REFERENCES MediaMetadata(MediaId) ON DELETE CASCADE,

    FileResolution INT,
    FileCodec VARCHAR(10),
    FileFramerate INT,
    FileSubtitles BIT,
    FileSize INT,


    PRIMARY KEY(FilePath)
);
