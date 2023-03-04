## microgrid-model
 This is a package helps to create a operational control model of microgrid. 
 In this package, mathematical models are used to describe operational of 
 various components of the MG. The components like renewable unit, 
 thermal generator, battery storage and the underlying electrical network. 
 This package includes data loaders to simulate the Microgrid model. Currently this data is injected as csv files but however this injection is   abstracted so that data can be obtained from any source. 

Along with the simulator module, a control module that predicts the behaviour of the MG and select optimal operational set-points is also included. The operational set-points are selected through solving an MPC problem. 
