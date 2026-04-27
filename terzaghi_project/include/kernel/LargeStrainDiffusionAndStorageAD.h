#pragma once
#include "ADTimeKernel.h"

class LargeStrainDiffusionAndStorageAD : public ADTimeKernel
{
public:
  static InputParameters validParams();
  LargeStrainDiffusionAndStorageAD(const InputParameters & params);

protected:
  virtual ADReal computeQpResidual() override;

  Real _k0_mu; // Initial mobility
  Real _m_v;
  Real _e0;    // Initial void ratio

  const ADVariableGradient & _grad_ux;
  const ADVariableGradient & _grad_uy;
};