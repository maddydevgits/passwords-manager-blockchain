// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract PasswordsManager {

  string[] _usernames;
  string[] _passwords;
  string[] _secretkeys;

  uint[] _ids;
  string[] _owners;
  string[] _websitenames;
  string[] _websiteusernames;
  string[] _websitepasswords;
  string[] _websitenotes;

  mapping(string=>bool) _registeredusers;
  uint id;

  constructor(){
    id=0;
  }

  function addUser(string memory username,string memory password,string memory secretkey) public {
    require(!_registeredusers[username]);
    
    _usernames.push(username);
    _passwords.push(password);
    _secretkeys.push(secretkey);
    _registeredusers[username]=true;
  }

  function viewUsers() public view returns(string[] memory,string[] memory,string[] memory){
    return (_usernames,_passwords,_secretkeys);
  }

  function addPassword(string memory owner,string memory website,string memory username,string memory password,string memory notes) public {
    id+=1;
    _ids.push(id);
    _owners.push(owner);
    _websitenames.push(website);
    _websiteusernames.push(username);
    _websitepasswords.push(password);
    _websitenotes.push(notes);
  }

  function viewPasswords() public view returns(uint[] memory,string[] memory,string[] memory,string[] memory,string[] memory,string[] memory) {
    return(_ids,_owners,_websitenames,_websiteusernames,_websitepasswords,_websitenotes);
  }

  function updatePassword(uint id1,string memory website,string memory username,string memory password, string memory notes) public {
    uint i;

    for(i=0;i<_ids.length;i++){
      if(_ids[i]==id1){
        _websitenames[i]=website;
        _websiteusernames[i]=username;
        _websitepasswords[i]=password;
        _websitenotes[i]=notes;
      }
    }
  }

  function deletePassword(uint id1) public{
    uint i;
    for(i=0;i<_ids.length;i++){
      if (id1==_ids[i]) {
        _owners[i]="";
      }
    }
  }

}
