use std::{
    io::{
        Error,
        ErrorKind
    },
    net::IpAddr
};
use serde::Deserialize;
use std::option::Option;

#[derive(Deserialize, PartialEq, Eq, Debug, Default)]
pub struct Plan {
    instances: Vec<IpAddr>,
    image: String,
    configs: Vec<String>,
}

impl Plan {

    pub fn validate(self) -> Option<Error> {
        if self.instances.len() == 0 {
            return Some(Error::new(
                ErrorKind::InvalidData,
                "At least one instance must be specified"
            ));
        }
        if self.instances.len() != self.configs.len() || self.configs.len() != 1 {
            return Some(Error::new(
                ErrorKind::InvalidData,
                "Must provide a 1:1 mapping of instances to configurations or a single configuration for all instances"
            ));
        }
        return None;
    }

}
