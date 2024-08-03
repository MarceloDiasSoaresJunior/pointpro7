@extends('templates.company')
@section('content')

<!-- ============ Main content start ============= -->
<div class="main-content">

    <div class="breadcrumb">
        <h1 class="me-2">Funções</h1>
        <!--  <ul>
    <li><a href="">Dashboard</a></li>
    <li>Version 1</li>
  </ul> -->
    </div>

    <div class="separator-breadcrumb border-top"></div>

    <div class="row">

        <div class="col-md-12 mb-4">
            <div class="card text-start">
                <div class="card-body">
                    <h4 class="card-title mb-3 w-50 float-start ">
                        <span class="text-primary" style="vertical-align: middle;">
                            <i class="i-Library" style="font-size: 26px;margin-right: 8px;"></i>
                        </span> Gerenciamento de cargos e funções
                    </h4>
                    <div class="dropdown dropleft text-end w-50 float-end">
                        <button class="btn btn-success btn-icon text-white" id="dropdownMenuButton_table2" type="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="width: 111px;margin-bottom: 10px!important;">
                            <span class="ul-btn__icon">
                                <i class="i-Add"></i>
                            </span>
                            <span class="ul-btn__text"> Adicionar</span>
                        </button>
                        <div class="dropdown-menu" aria-labelledby="dropdownMenuButton_table2">
                            <a class="dropdown-item" href="/funcoes/adicionar-nova">Adicionar nova Função</a>
                        </div>
                    </div>
                    <p class="w-50">
                        Realize a gestão do cadastro dos cargos e <code><b>funções</b></code>:
                    </p>


                    <div class="">
                        @if($funcoes->count())
                        <div class="table-responsive">
                            <table class="table table-hover table-striped ">
                                <thead style="text-align: center;">
                                    <tr>
                                        <th scope="col">#</th>
                                        <th scope="col">Função</th>
                                        <th scope="col">Onboarding</th>
                                        <th scope="col">Atividades</th>
                                        <th scope="col">Editar</th>
                                        <th scope="col">Apagar</th>
                                    </tr>
                                </thead>
                                <tbody style="text-align: center;">
                                    @foreach($funcoes as $funcao)
                                    <tr>
                                        <th scope="row">{{ $funcao->id }}</th>
                                        <td>{{ $funcao->title }}</td>
                                        <td>
                                            @if($funcao->onboarding)
                                            <a href="{{ $funcao->onboarding }}" target="_blank">Baixar</a>
                                            @else
                                            Arquivo nao encontrado
                                            @endif
                                        </td>
                                        <td>{{ $funcao->atividades()->count() }}</td>
                                        <td style="padding-bottom: 3px;">
                                            <a class="text-warning me-2" style="font-size: 26px;" href="#" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                                <i class="nav-icon i-Pen-5 fw-bold"></i>
                                            </a>
                                            <div class="dropdown-menu menu-opcoes" x-placement="bottom-start">
                                                <a class="dropdown-item ul-widget__link--font" href="/funcoes/{{ $funcao->id }}/editar">Editar</a>
                                            </div>
                                        </td>
                                        <td style="padding-bottom: 3px;">
                                            <a class="text-danger me-2" style="font-size: 26px;" href="#" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                                <i class="nav-icon i-Close-Window fw-bold"></i>
                                            </a>
                                            <div class="dropdown-menu menu-opcoes" x-placement="bottom-start">
                                                <a class="dropdown-item ul-widget__link--font" href="/funcoes/{{ $funcao->id }}/deletar">Apagar</a>
                                            </div>
                                        </td>
                                    </tr>
                                    @endforeach

                                </tbody>
                            </table>
                        </div>
                        @else
                        <div class="alert alert-dismissible fade show alert-card alert-info" role="alert">
                            <strong class="text-capitalize">Nenhuma funcao cadastrada</strong>
                        </div>
                        @endif
                    </div>




                </div>
            </div>
        </div>

    </div>
    <!-- end of row -->
</div>
<!-- ======= Main content end ======= -->
@endsection