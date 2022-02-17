"""Package contains all Resources used in this server"""
from api.resources.getImages import OneFullsize, MultipleFullsize, OneThumbnail, MultipleThumbnails, AllThumbnails
from api.resources.getMetadata import AllPictureIDs, MetadataOneImage, MetadataMultipleImages, MetadataAllImages, ImagesSize, ThumbnailSize, AnalyseDataset
from api.resources.getNn import Upload, NNOfExistingImage, NNOfExistingImages
from api.resources.misc import GetAllFaissIndices, ChangeActiveFaissIndex, ChangeNumberOfKMeansCentroids, GetSessionToken

__all__ = [
    "OneFullsize",
    "MultipleFullsize",
    "OneThumbnail",
    "MultipleThumbnails",
    "AllThumbnails",
    "AllPictureIDs",
    "MetadataOneImage",
    "MetadataMultipleImages",
    "MetadataAllImages",
    "ImagesSize",
    "ThumbnailSize",
    "AnalyseDataset",
    "Upload",
    "NNOfExistingImage",
    "NNOfExistingImages",
    "GetAllFaissIndices",
    "ChangeActiveFaissIndex",
    "ChangeNumberOfKMeansCentroids",
    "GetSessionToken"
]