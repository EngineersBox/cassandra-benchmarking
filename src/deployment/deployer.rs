use ssh2::Session;
use std::option::Option;
use crate::plan::plan::Plan;
use std::io::{Error, ErrorKind};

pub struct Deployer {
    session: Option<Session>,
    plan: Plan,
}

impl Deployer {

    pub fn new(plan: &Plan) -> Deployer {
        Deployer {
            session: None,
            plan,
        }
    }

    pub fn deploy(self) -> Option<Error> {
        
        return None;
    }

}
