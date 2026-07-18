CREATE TABLE IF NOT EXISTS default.content
(
    tconst String,
    titleType String,
    primaryTitle String,
    originalTitle String,
    isAdult UInt8,
    startYear Nullable(UInt16),
    endYear Nullable(UInt16),
    runtimeMinutes Nullable(UInt32),
    genres String,
    averageRating Nullable(Float32),
    numVotes Nullable(UInt32),
    releaseYear UInt16
)
ENGINE = MergeTree()
ORDER BY (titleType, releaseYear, tconst);
