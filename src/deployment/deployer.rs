use ssh2::Session;
use tokio::task::JoinSet;
use crate::{net::ssh::SessionProvider, plan::plan::Plan};
use std::io::{Error, ErrorKind};

pub struct Deployer {
    pub plan: Plan,
}

impl Deployer {

    pub fn new(plan: &Plan) -> Deployer {
        Deployer {
            plan,
        }
    }

    fn deploy_instance(session_provider: SessionProvider, ssh_user: String, config_path: String) -> Result<(), Error> {
        let mut session: Session = session_provider.provide()?;
        SessionProvider::authenticate(&mut session, ssh_user.as_str())?;
        Ok(())
    }

    pub async fn deploy(&self, ssh_user: &String) -> Result<JoinSet<Result<(),Error>>, Error> {
        let mut set: JoinSet<Result<(),Error>> = JoinSet::new();
        for (name,target) in self.plan.instances.iter() {
            let config_path = match self.plan.configs.get(name) {
                Some(path) => path.clone(),
                None => {
                    set.abort_all();
                    return Err(Error::new(ErrorKind::InvalidInput, format!("No config for {}", name)));
                }
            };
            let thread_session: SessionProvider = SessionProvider::new(target.clone());
            let thread_ssh_user: String = ssh_user.clone();
            set.spawn(async move {
                Deployer::deploy_instance(thread_session, thread_ssh_user, config_path)
            });
        }
        Ok(set)
    }

}
