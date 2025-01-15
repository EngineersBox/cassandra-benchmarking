use std::io::Error;
use ssh2::Channel;

pub trait Application {

    fn name() -> String;

    fn write_payload(&self, channel: &mut Channel) -> Result<(), Error>;

}
