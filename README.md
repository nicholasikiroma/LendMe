# Project Title: LendME

![landing page](./img/Screenshot%20from%202023-07-14%2018-21-23.png)

## Description

LendME is a peer-to-peer lending platform designed to facilitate lending transactions between individuals.
It offers users the opportunity to put their excess funds to work by lending them out to borrowers in need,
while earning an interest on their investment. It's a win-win experience for both lender and borrower.

## Project Architecture

LendME was built following the microservices architecture. Key essential functions of the platform was split into indepently deployable services.

![project architecture](./img/Screenshot%202023-06-29%20at%2014-58-07%20How%20to%20Design%20a%20Web%20Application%20Software%20Architecture%20101.png)

The services are as follows:

- [User Management Service](./user): This service is responsible for the creation, authorization, and authentication of users.
- [Loan Management Service](./loan/): This service is solely responsible for handling everything concerning loan operations such as creation, deletion, loan applications, and for determining the interest added on a loan based on the date a loan is started and the day it a repayment is initiated.
- [Wallet Management Service](./payment/): This service is responsible for creating a virtual wallet new users, funding of wallet, and managing wallet-to-wallet transactions.
- [Risk Assessment Service](./risk/): This service is responsible for tracking the financial profile of potential borrowers and generating risk assessment reports to inform potential lenders if a particular client is eligible for a loan they're offering or not.
- [Frontend Interface](./frontend/): The interface is responsible for commmunicating with other RESTful services over HTTP and renders dynamic templates to clients.

## Usage

Each service can be run indepently(check readme of services to see how they are run).

## API Client

Insomnia was used to test all API endpoints.
