const PasswordsManager=artifacts.require('PasswordsManager');

module.exports=function(deployer){
    deployer.deploy(PasswordsManager);
}