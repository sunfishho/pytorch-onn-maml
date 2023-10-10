"""
Description:
Author: Jiaqi Gu (jqgu@utexas.edu)
Date: 2021-06-10 03:39:01
LastEditors: Jiaqi Gu (jqgu@utexas.edu)
LastEditTime: 2021-06-10 03:39:01
"""
import unittest
from pyutils.general import TimerCtx
import torch
import numpy as np
import torchonn_maml as onn
from pyutils.general import logger
from torchonn_maml.layers import (
    MZIConv2d,
    MZILinear,
    MZIBlockConv2d,
    MZIBlockLinear,
    FFTONNBlockLinear,
    FFTONNBlockConv2d,
    AllPassMORRCirculantLinear,
    AllPassMORRCirculantConv2d,
    AddDropMRRConv2d,
    AddDropMRRBlockConv2d,
    AddDropMRRLinear,
    AddDropMRRBlockLinear,
    PCMConv2d,
    PCMLinear,
    SuperBlockLinear,
    SuperBlockConv2d,
    super_layer_name_dict,
    get_named_sample_arch,
)


class TestLayers(unittest.TestCase):
    def test_mzilinear(self):
        device = torch.device("cuda:0")
        layer = MZILinear(8, 8, bias=False, mode="usv", device=device).to(device)
        layer.reset_parameters()
        x = torch.randn(1, 8, device=device)
        weight = layer.build_weight().data.clone()
        y = layer(x).detach()
        layer.switch_mode_to("phase")
        layer.sync_parameters(src="usv")
        weight2 = layer.build_weight().data.clone()
        y2 = layer(x).detach()
        # print(weight)
        # print(weight2)
        # print(y)
        # print(y2)

        assert np.allclose(weight.cpu().numpy(), weight2.cpu().numpy(), rtol=1e-4, atol=1e-4), print(
            "weight max abs error:", np.abs(weight.cpu().numpy() - weight2.cpu().numpy()).max()
        )
        assert np.allclose(y.cpu().numpy(), y2.cpu().numpy(), rtol=1e-4, atol=1e-4), print(
            "result max abs error:", np.abs(y.cpu().numpy() - y2.cpu().numpy()).max()
        )

        # test layer conversion
        linear = torch.nn.Linear(8, 8, bias=True).to(device)
        layer = MZILinear.from_layer(linear, mode="phase", photodetect=False)
        y1 = linear(x).detach().cpu().numpy()
        y2 = layer(x).detach().cpu().numpy()
        # print(y1)
        # print(y2)

        assert np.allclose(y1, y2, rtol=1e-4, atol=1e-4), print(
            "converted result max abs error:", np.abs(y1 - y2).max()
        )

    def test_mziconv2d(self):
        device = torch.device("cuda:0")
        layer = MZIConv2d(8, 8, 3, bias=False, mode="usv", device=device).to(device)
        layer.reset_parameters()
        x = torch.randn(1, 8, 4, 4, device=device)
        weight = layer.build_weight().data.clone()
        y = layer(x).detach()
        layer.switch_mode_to("phase")
        layer.sync_parameters(src="usv")
        weight2 = layer.build_weight().data.clone()
        y2 = layer(x).detach()
        # print(weight)
        # print(weight2)
        # print(y)
        # print(y2)

        assert np.allclose(weight.cpu().numpy(), weight2.cpu().numpy(), rtol=1e-4, atol=1e-4), print(
            "max abs error:", np.abs(weight.cpu().numpy() - weight2.cpu().numpy()).max()
        )
        assert np.allclose(y.cpu().numpy(), y2.cpu().numpy(), rtol=1e-4, atol=1e-4), print(
            "max abs error:", np.abs(y.cpu().numpy() - y2.cpu().numpy()).max()
        )

        # test layer conversion
        conv2d = torch.nn.Conv2d(8, 8, 3, stride=2, bias=True).to(device)
        layer = MZIConv2d.from_layer(conv2d, mode="phase", photodetect=False)
        y1 = conv2d(x).detach().cpu().numpy()
        y2 = layer(x).detach().cpu().numpy()
        # print(y1)
        # print(y2)

        assert np.allclose(y1, y2, rtol=1e-4, atol=1e-4), print("max abs error:", np.abs(y1 - y2).max())

    def test_mziblocklinear(self):
        device = torch.device("cuda:0")
        fc = MZIBlockLinear(8, 8, bias=False, miniblock=4, mode="usv", device=device).to(device)
        fc.reset_parameters()
        x = torch.randn(1, 8, device=device)
        weight = fc.build_weight().data.clone()
        y = fc(x).detach()
        fc.switch_mode_to("phase")
        fc.sync_parameters(src="usv")
        weight2 = fc.build_weight().data.clone()
        y2 = fc(x).detach()
        # print(weight)
        # print(weight2)
        # print(y)
        # print(y2)

        assert np.allclose(weight.cpu().numpy(), weight2.cpu().numpy(), rtol=1e-4, atol=1e-4), print(
            "weight max abs error:", np.abs(weight.cpu().numpy() - weight2.cpu().numpy()).max()
        )
        assert np.allclose(y.cpu().numpy(), y2.cpu().numpy(), rtol=1e-4, atol=1e-4), print(
            "result max abs error:", np.abs(y.cpu().numpy() - y2.cpu().numpy()).max()
        )

        # test layer conversion
        linear = torch.nn.Linear(8, 8, bias=True).to(device)
        layer = MZIBlockLinear.from_layer(linear, miniblock=4, mode="phase", photodetect=False)
        y1 = linear(x).detach().cpu().numpy()
        y2 = layer(x).detach().cpu().numpy()
        # print(y1)
        # print(y2)

        assert np.allclose(y1, y2, rtol=1e-4, atol=1e-4), print(
            "converted result max abs error:", np.abs(y1 - y2).max()
        )

    def test_mziblockconv2d(self):
        device = torch.device("cuda:0")
        conv2d = MZIBlockConv2d(8, 8, 3, bias=False, miniblock=4, mode="usv", device=device).to(device)
        conv2d.reset_parameters()
        x = torch.randn(1, 8, 4, 4, device=device)
        weight = conv2d.build_weight().data.clone()
        y = conv2d(x).detach()
        conv2d.switch_mode_to("phase")
        conv2d.sync_parameters(src="usv")
        weight2 = conv2d.build_weight().data.clone()
        y2 = conv2d(x).detach()
        # print(weight)
        # print(weight2)
        # print(y)
        # print(y2)

        assert np.allclose(weight.cpu().numpy(), weight2.cpu().numpy(), rtol=1e-4, atol=1e-4), print(
            "weight max abs error:", np.abs(weight.cpu().numpy() - weight2.cpu().numpy()).max()
        )
        assert np.allclose(y.cpu().numpy(), y2.cpu().numpy(), rtol=1e-4, atol=1e-4), print(
            "result max abs error:", np.abs(y.cpu().numpy() - y2.cpu().numpy()).max()
        )

        # test layer conversion
        conv2d = torch.nn.Conv2d(8, 8, 3, stride=2, bias=True).to(device)
        layer = MZIBlockConv2d.from_layer(conv2d, miniblock=4, mode="phase", photodetect=False)
        y1 = conv2d(x).detach().cpu().numpy()
        y2 = layer(x).detach().cpu().numpy()
        # print(y1)
        # print(y2)

        assert np.allclose(y1, y2, rtol=1e-4, atol=1e-4), print(
            "converted result max abs error:", np.abs(y1 - y2).max()
        )

    # def test_fftonnblocklinear(self):
    #     device = torch.device("cuda:0")
    #     layer = FFTONNBlockLinear(8, 8, bias=False, miniblock=4, mode="fft", device=device).to(device)
    #     layer.reset_parameters(mode="fft")
    #     layer.set_input_bitwidth(8)
    #     layer.set_weight_bitwidth(8)
    #     x = torch.randn(1, 8, device=device)
    #     weight = layer.build_weight().data.clone()
    #     y = layer(x).detach()
    #     print(weight)
    #     print(y)

    # def test_fftonnblockconv2d(self):
    #     device = torch.device("cuda:0")
    #     layer = FFTONNBlockConv2d(8, 8, 3, bias=False, miniblock=4, mode="fft", device=device).to(device)
    #     layer.reset_parameters(mode="fft")
    #     layer.set_input_bitwidth(8)
    #     layer.set_weight_bitwidth(8)
    #     x = torch.randn(1, 8, 4, 4, device=device)
    #     weight = layer.build_weight().data.clone()
    #     y = layer(x).detach()
    #     print(weight)
    #     print(y)

    # def test_allpassmorrcirculantlinear(self):
    #     device = torch.device("cuda:0")
    #     layer = AllPassMORRCirculantLinear(
    #         8,
    #         8,
    #         bias=True,
    #         miniblock=4,
    #         morr_init=True,
    #         trainable_morr_scale=True,
    #         trainable_morr_bias=True,
    #         device=device,
    #     ).to(device)
    #     layer.reset_parameters(morr_init=True)
    #     layer.set_input_bitwidth(8)
    #     layer.set_weight_bitwidth(8)
    #     x = torch.randn(1, 8, device=device)
    #     weight = layer.build_weight()[0].data.clone()
    #     y = layer(x).detach()
    #     print(weight)
    #     print(y)

    # def test_allpassmorrcirculantconv2d(self):
    #     device = torch.device("cuda:0")
    #     layer = AllPassMORRCirculantConv2d(
    #         8,
    #         8,
    #         3,
    #         bias=True,
    #         miniblock=4,
    #         morr_init=True,
    #         trainable_morr_scale=True,
    #         trainable_morr_bias=True,
    #         device=device,
    #     ).to(device)
    #     layer.reset_parameters(morr_init=True)
    #     layer.set_input_bitwidth(8)
    #     layer.set_weight_bitwidth(8)
    #     x = torch.randn(1, 8, 4, 4, device=device)
    #     weight = layer.build_weight().data.clone()
    #     y = layer(x).detach()
    #     print(weight)
    #     print(y)

    # def test_pcmconv2d(self):
    #     device = torch.device("cuda:0")
    #     layer = PCMConv2d(
    #         8,
    #         8,
    #         3,
    #         bias=True,
    #         block_size=8,
    #         mode="block",
    #         device=device,
    #     ).to(device)
    #     layer.reset_parameters()
    #     layer.set_input_bitwidth(8)
    #     layer.set_weight_bitwidth(8)
    #     x = torch.randn(1, 8, 4, 4, device=device)
    #     weight = layer.build_weight().data.clone()
    #     y = layer(x).detach()
    #     print(weight)
    #     print(y)

    # def test_pcmlinear(self):
    #     device = torch.device("cuda:0")
    #     layer = PCMLinear(
    #         8,
    #         8,
    #         bias=True,
    #         block_size=8,
    #         mode="block",
    #         device=device,
    #     ).to(device)
    #     layer.reset_parameters()
    #     layer.set_input_bitwidth(8)
    #     layer.set_weight_bitwidth(8)
    #     x = torch.randn(1, 8, device=device)
    #     weight = layer.build_weight().data.clone()
    #     y = layer(x).detach()
    #     print(weight)
    #     print(y)

    # def test_superblocklinear(self):
    #     device = torch.device("cuda:0")
    #     arch = dict(
    #         n_waveguides=4,
    #         n_blocks=4,
    #         n_layers_per_block=2,
    #         n_front_share_blocks=4,
    #         share_ps="row_col",
    #         interleave_dc=True,
    #         symmetry_cr=False,
    #         device_cost=dict(
    #             ps_weight=6.8,
    #             dc_weight=1.5,
    #             cr_weight=0.064,
    #             area_upper_bound=120,
    #             area_lower_bound=70,
    #             first_active_block=True,
    #         ),
    #     )

    #     super_layer = super_layer_name_dict["adept"](arch=arch, device=device)

    #     layer = SuperBlockLinear(
    #         8,
    #         8,
    #         bias=True,
    #         miniblock=4,
    #         super_layer=super_layer,
    #         device=device,
    #     ).to(device)
    #     layer.reset_parameters()
    #     layer.set_input_bitwidth(8)
    #     layer.set_weight_bitwidth(8)
    #     x = torch.randn(1, 8, device=device)
    #     super_layer.build_arch_mask("gumbel_soft")
    #     weight = layer.build_weight().data.clone()
    #     y = layer(x).detach()
    #     print(weight)
    #     print(y)

    # def test_superblockconv2d(self):
    #     device = torch.device("cuda:0")
    #     # arch definition
    #     arch = dict(
    #         n_waveguides=4,
    #         n_blocks=4,
    #         n_layers_per_block=2,
    #         n_front_share_blocks=4,
    #         share_ps="row_col",
    #         interleave_dc=True,
    #         symmetry_cr=False,
    #         device_cost=dict(
    #             ps_weight=6.8,
    #             dc_weight=1.5,
    #             cr_weight=0.064,
    #             area_upper_bound=120,
    #             area_lower_bound=70,
    #             first_active_block=True,
    #         ),
    #     )

    #     # use the arch definition to create a super optical layer
    #     super_layer = super_layer_name_dict["adept"](arch=arch, device=device)

    #     # when creating the super conv2d, pass the super_layer to it
    #     layer = SuperBlockConv2d(
    #         8,
    #         8,
    #         3,
    #         bias=True,
    #         miniblock=4,
    #         super_layer=super_layer,
    #         device=device,
    #     ).to(device)
    #     layer.reset_parameters()
    #     layer.set_input_bitwidth(8)
    #     layer.set_weight_bitwidth(8)
    #     x = torch.randn(1, 8, 4, 4, device=device)

    #     # explicitly build the architecture mask during each training iteration before forward
    #     super_layer.build_arch_mask("gumbel_soft")
    #     weight = layer.build_weight().data.clone()
    #     y = layer(x).detach()
    #     print(weight)
    #     print(y)

    def test_mrrconv2d(self):
        device = torch.device("cuda:0")
        layer = AddDropMRRConv2d(
            8,
            8,
            3,
            bias=True,
            mode="weight",
            device=device,
        ).to(device)
        layer.reset_parameters()
        layer.set_input_bitwidth(8)
        layer.set_weight_bitwidth(8)
        x = torch.randn(1, 8, 4, 4, device=device)
        weight = layer.build_weight().data.clone()
        y = layer(x).detach()
        print(weight)
        print(y)
    
    def test_mrrblockconv2d(self):
        device = torch.device("cuda:0")
        layer = AddDropMRRBlockConv2d(
            8,
            8,
            3,
            miniblock=4,
            bias=True,
            mode="weight",
            device=device,
        ).to(device)
        layer.reset_parameters()
        layer.set_input_bitwidth(8)
        layer.set_weight_bitwidth(8)
        x = torch.randn(1, 8, 4, 4, device=device)
        weight = layer.build_weight().data.clone()
        y = layer(x).detach()
        print(weight)
        print(y)
    
    def test_mrrlinear(self):
        device = torch.device("cuda:0")
        layer = AddDropMRRLinear(
            8,
            8,
            bias=True,
            mode="weight",
            device=device,
        ).to(device)
        layer.reset_parameters()
        layer.set_input_bitwidth(8)
        layer.set_weight_bitwidth(8)
        x = torch.randn(1, 8, device=device)
        weight = layer.build_weight().data.clone()
        y = layer(x).detach()
        print(weight)
        print(y)
    
    def test_mrrblocklinear(self):
        device = torch.device("cuda:0")
        layer = AddDropMRRBlockLinear(
            8,
            8,
            miniblock=4,
            bias=True,
            mode="weight",
            device=device,
        ).to(device)
        layer.reset_parameters()
        layer.set_input_bitwidth(8)
        layer.set_weight_bitwidth(8)
        x = torch.randn(1, 8, device=device)
        weight = layer.build_weight().data.clone()
        y = layer(x).detach()
        print(weight)
        print(y)

if __name__ == "__main__":
    unittest.main()
