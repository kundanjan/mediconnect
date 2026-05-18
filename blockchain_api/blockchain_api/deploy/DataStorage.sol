// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataStorage {
    struct UserProfile {
        string data; // JSON string containing all user data
        address ethereumAddress;
        string username;
    }

    struct LabReport {
        string reportData; // JSON string containing report data
    }

    struct DoctorProfile {
        string data; // JSON string containing all doctor data
        address ethereumAddress;
    }

    mapping(string => UserProfile) public userProfiles; // Access code to UserProfile
    mapping(string => UserProfile) public userProfilesByUsername; // Username to UserProfile
    mapping(string => LabReport[]) public labReports;
    mapping(address => string) public userAccessCodes;
    mapping(string => DoctorProfile) public doctorProfiles;

    function storeUserProfile(string memory _accessCode, string memory _data, string memory _username) public {
        require(bytes(userProfilesByUsername[_username].username).length == 0, "Username already exists");
        UserProfile memory newProfile = UserProfile(_data, msg.sender, _username);
        userProfiles[_accessCode] = newProfile;
        userProfilesByUsername[_username] = newProfile;
        userAccessCodes[msg.sender] = _accessCode;
    }

    function getUserProfile(string memory _accessCode) public view returns (string memory, address, string memory) {
        UserProfile memory user = userProfiles[_accessCode];
        return (user.data, user.ethereumAddress, user.username);
    }

    function getUserProfileByUsername(string memory _username) public view returns (string memory, address, string memory) {
        UserProfile memory user = userProfilesByUsername[_username];
        return (user.data, user.ethereumAddress, user.username);
    }

    function storeLabReport(string memory _reportData, string memory _accessCode) public {
        require(userProfiles[_accessCode].ethereumAddress == msg.sender, "Not authorized");
        labReports[_accessCode].push(LabReport(_reportData));
    }

    function getLabReports(string memory _accessCode) public view returns (LabReport[] memory) {
        return labReports[_accessCode];
    }

    function getLabReportCount(string memory _accessCode) public view returns (uint) {
        return labReports[_accessCode].length;
    }

    function getMyAccessCode() public view returns (string memory) {
        return userAccessCodes[msg.sender];
    }

    function storeDoctorProfile(string memory _username, string memory _data) public {
        doctorProfiles[_username] = DoctorProfile(_data, msg.sender);
    }

    function getDoctorProfile(string memory _username) public view returns (string memory, address) {
        DoctorProfile memory doctor = doctorProfiles[_username];
        return (doctor.data, doctor.ethereumAddress);
    }
}