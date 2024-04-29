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

use std::io::BufReader;
use std::fs::File;
use ssh2::Session;

pub(crate) use lazy_static::lazy_static;
use slog::Logger;

use crate::logging::logging::initialize_logging;
use crate::plan::plan::Plan;
use crate::deployment::deployer::Deployer;

lazy_static!{
    static ref LOGGER: Logger = initialize_logging(String::from("Deployer"));
}

fn main() {
    info!(&crate::LOGGER, "Configured logger");
    let plan_path: String = match std::env::args().nth(1) {
        Some(p) => p,
        None => crit!(&crate::LOGGER, "Usage: deployer <plan> <ssh user>"),
    };
    let ssh_user: String = match std::env::args().nth(2) {
        Some(u) => u,
        None => crit!(&crate::LOGGER, "Usage: deployer <plan> <ssh user>"),
    };
    let plan_file: File = match File::open(plan_path) {
        Ok(f) => f,
        Err(e) => error!(&crate::LOGGER, "{}", e),
    };
    info!(&crate::LOGGER, "Parsing plan");
    let plan: Plan = match serde_json::from_reader(BufReader::new(plan_file)) {
        Ok(p) => p,
        Err(e) => error!(&crate::LOGGER, "{}", e),
    };
    match plan.validate() {
        Some(err) => error!(&crate::LOGGER, "Plan failed during validation: {}", err),
        None => {},
    }
    let deployer: Deployer = Deployer::new(&plan);
}
