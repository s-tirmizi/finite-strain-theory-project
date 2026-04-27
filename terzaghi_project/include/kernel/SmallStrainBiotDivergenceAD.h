#pragma once

#include "ADTimeKernel.h"

class SmallStrainBiotDivergenceAD : public ADTimeKernel
{
public:
  static InputParameters validParams();
  SmallStrainBiotDivergenceAD(const InputParameters & params);

protected:
  virtual ADReal computeQpResidual() override;

  const Real _B;
  const ADVariableValue & _u_x_dot; 
  const ADVariableValue & _u_y_dot; 
  const ADVariableGradient & _grad_u_x_dot;
  const ADVariableGradient & _grad_u_y_dot;
};