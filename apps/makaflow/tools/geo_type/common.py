from dataclasses import dataclass

@dataclass
class Type:
    Plain = 0
    Regex = 1
    RootDomain = 2
    Full = 3

@dataclass
class Domain:
    type:Type = 1
    value:str = 2
    
@dataclass
class CIDR:
    ip:bytes
    prefix:int
    ip_addr:str

@dataclass
class GeoIP:
    country_code:str
    cidr:list[CIDR]
    inverse_match:bool
    resource_hash:bytes
    code:str
    file_path:str
    
@dataclass
class GeoIPList:
     entry:list[GeoIP]

@dataclass
class GeoSite:
    country_code:str
    domain:list[Domain]
    resource_hash:bytes
    code:str
    file_path:str

@dataclass
class GeoSiteList:
     entry:list[GeoSite]
