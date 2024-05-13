mod logging;
mod net;
mod plan;
mod deployment;

extern crate serde;
extern crate serde_json;
extern crate ssh2;
extern crate flate2;
extern crate systemctl;
extern crate docker_api;
#[macro_use]
extern crate slog;
extern crate slog_term;
extern crate slog_async;
extern crate slog_json;
extern crate lazy_static;
extern crate tokio;

use std::io::BufReader;
use std::fs::File;
use std::io::{Error,ErrorKind};

pub(crate) use lazy_static::lazy_static;
use slog::Logger;
use tokio::task::JoinSet;

use crate::logging::logging::initialize_logging;
use crate::plan::plan::Plan;
use crate::deployment::deployer::Deployer;

lazy_static!{
    static ref LOGGER: Logger = initialize_logging(String::from("Deployer"));
}

async fn run() -> Result<(), std::io::Error> {
    info!(&crate::LOGGER, "Configured logger");
    let plan_path: String = match std::env::args().nth(1) {
        Some(p) => p,
        None => return Err(Error::new(
            ErrorKind::InvalidInput,
            "Usage: deployer <plan> <ssh user>"
        )),
    };
    let ssh_user: String = match std::env::args().nth(2) {
        Some(u) => u,
        None => return Err(Error::new(
            ErrorKind::InvalidInput,
            "Usage: deployer <plan> <ssh user>"
        )),
    };
    let plan_file: File = File::open(plan_path)?;
    info!(&crate::LOGGER, "Parsing plan");
    let plan: Plan = serde_json::from_reader(BufReader::new(plan_file))?;
    match plan.validate() {
        Some(err) => return Err(Error::new(
            ErrorKind::InvalidData,
            format!("Plan failed during validation: {}", err).as_str()
        )),
        None => {},
    }
    let deployer: Deployer = Deployer::new(&plan);
    let mut set: JoinSet<Result<(), Error>> = deployer.deploy(&ssh_user).await?;
    while let Some(result) = set.join_next().await {
        match result {
            Err(e) => return Err(Error::new(
                ErrorKind::Other,
                e.to_string()
            )),
            Ok(Err(e)) => return Err(e),
            _ => {}
        }
    }
    Ok(())
}

#[tokio::main]
async fn main() {
    match run().await {
        Ok(()) => {},
        Err(e) => error!(&crate::LOGGER, "{}", e)
    }
}
